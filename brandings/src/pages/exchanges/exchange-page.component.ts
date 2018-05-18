import { ChangeDetectionStrategy, Component, OnInit, ViewEncapsulation } from '@angular/core';
import { NavController, NavParams, Platform } from 'ionic-angular';
import { Observable } from 'rxjs/Observable';
import { ExchangeInfo } from '../../interfaces/exchange.interfaces';
import { ExchangesService } from '../../services/exchanges.service';
import { ExchangeDetailPageComponent } from './exchange-detail-page.component';

@Component({
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: 'exchange-page.component.html',
})
export class ExchangesPageComponent implements OnInit {

  public exchanges$: Observable<ExchangeInfo[]>;

  constructor(private navParams: NavParams,
              private platform: Platform,
              private navControl: NavController,
              private exchangeService: ExchangesService) {
  }

  ngOnInit() {
    this.exchanges$ = this.exchangeService.getExchanges();
  }

  itemSelected(item: ExchangeInfo) {
    this.navControl.push(ExchangeDetailPageComponent, {info: item});
  }

  close() {
    this.platform.exitApp();
  }
}
